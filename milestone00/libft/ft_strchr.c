/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_strchr.c                                        :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: kyonaha <kyonaha@student.42tokyo.jp>       +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2026/04/24 13:45:52 by kyonaha           #+#    #+#             */
/*   Updated: 2026/05/01 15:28:12 by kyonaha          ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

char	*ft_strchr(const char *str, int chr)
{
	while (*str != (unsigned char)chr && *str != '\0')
		str++;
	if (*str == (unsigned char)chr)
		return ((char *)str);
	return (NULL);
}
