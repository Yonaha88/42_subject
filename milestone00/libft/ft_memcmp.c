/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memcmp.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/25 14:46:04 by kyonaha           #+#    #+#             */
/*   Updated: 2026/04/28 16:29:48 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

int	ft_memcmp(const void *src1, const void *src2, size_t num)
{
	size_t			idx;
	unsigned char	*s1;
	unsigned char	*s2;

	idx = 0;
	s1 = (unsigned char *)src1;
	s2 = (unsigned char *)src2;
	while (idx < num && s1[idx] == s2[idx])
		idx++;
	if (idx == num)
		return (0);
	return ((int)(s1[idx] - s2[idx]));
}
