/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memmove.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/24 10:27:12 by kyonaha           #+#    #+#             */
/*   Updated: 2026/04/28 16:29:38 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memmove(void *dest, const void *src, size_t num)
{
	if ((unsigned char *)dest < (unsigned char *)src)
		return (ft_memcpy(dest, src, num));
	else
	{
		while (0 < num)
		{
			((unsigned char *)dest)[num - 1] = ((unsigned char *)src)[num - 1];
			num--;
		}
		return (dest);
	}
}
